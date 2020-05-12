import unittest
import tests.test_book_reader as t


def suite():
    suite = unittest.TestSuite()
    suite.addTest(t.TestBookReader('test_load_line'))
    suite.addTest(t.TestBookReader('test_load_top'))
    suite.addTest(t.TestDataWorkflow('test_data_workflow'))
    suite.addTest(t.TestDataWorkflow('test_data_workflow_cache'))

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
