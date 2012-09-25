import contextlib
from os import path
import unittest
import errno
import shutil
import tempfile
import yapp
from yapp import core

class YappTest(unittest.TestCase):
    def setUp(self):
        self.my_dir = tempfile.mkdtemp()

    def tearDown(self):
        try:
            shutil.rmtree(self.my_dir)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

    def writeConfig(self, name, config_string):
        with open(path.join(self.my_dir, name+yapp.CONFIG_EXTENSION), 'w') as f:
            f.write(config_string)

    def copyFixture(self, filename):
        shutil.copy(path.join(path.dirname(__file__), 'fixtures', filename), path.join(self.my_dir, filename))

    @contextlib.contextmanager
    def fileAsString(self, *file):
        with open(path.join(self.my_dir, *file), 'r') as f:
            yield f.read()


    def assertFileExists(self, *file):
        self.assertTrue(path.exists(path.join(self.my_dir, *file)))
    def assertFileDoesNotExist(self, *file):
        self.assertFalse(path.exists(path.join(self.my_dir, *file)))


class TestSuccessfulRun(YappTest):
    def setUp(self):
        super().setUp()
        self.writeConfig('uppercase',
        """
        input_file_pattern: '*.txt'
        command: 'python -c "import sys;open(\\"side_effect.txt\\",\\"w\\").write(\\"SIDE EFFECT\\");sys.stdout.write(sys.stdin.read().upper())" < {input_file}'
        """)
        self.copyFixture('test.txt')
        yapp.core.processDir(self.my_dir)

    def testFiles(self):
        self.assertFileDoesNotExist('uppercase', 'test.txt.working')
        self.assertFileDoesNotExist('uppercase', 'test.txt.err')
        self.assertFileExists('uppercase', 'test.txt')
        self.assertFileExists('uppercase', 'side_effect.txt')

    def testFileContents(self):
        with self.fileAsString('test.txt') as input, self.fileAsString('uppercase', 'test.txt') as output:
            self.assertEqual(input.upper(), output)

class TestFailedRun(YappTest):
    def setUp(self):
        super().setUp()
        self.writeConfig('uppercase',
            """
            input_file_pattern: '*.txt'
            command: 'python -c "import sys;sys.stdout.write(\\"I WAS HALF WAY THROUGH THAT\\");sys.stderr.write(\\"OMG AN ERROR\\");sys.exit(127)" < {input_file}'
            """)
        self.copyFixture('test.txt')
        yapp.core.processDir(self.my_dir)

    def testFiles(self):
        self.assertFileExists('uppercase', 'test.txt.working')
        self.assertFileExists('uppercase', 'test.txt.err')
        self.assertFileDoesNotExist('uppercase', 'test.txt')

    def testWorkingFileContents(self):
        with self.fileAsString('uppercase', 'test.txt.working') as output:
            self.assertEqual("I WAS HALF WAY THROUGH THAT", output)

    def testStderrFileContents(self):
        with self.fileAsString('uppercase', 'test.txt.err') as output:
            self.assertEqual("OMG AN ERROR", output)

class TestNoopOnNothingToDo(TestSuccessfulRun):
    def setUp(self):
        super().setUp()

    def testNoop(self):
        #Store the current mtime of the output
        get_time = lambda: path.getmtime(path.join(self.my_dir, 'uppercase', 'test.txt'))
        old_time = get_time()
        yapp.core.processDir(self.my_dir)
        self.assertEqual(old_time, get_time())

class TestReprocessOnChange(TestSuccessfulRun):
    def setUp(self):
        super().setUp()

    def testReprocess(self):
        #Store the current mtime of the output
        get_time = lambda: path.getmtime(path.join(self.my_dir, 'uppercase', 'test.txt'))
        old_time = get_time()
        self.copyFixture('test.txt')
        yapp.core.processDir(self.my_dir)
        self.assertNotEqual(old_time, get_time())
