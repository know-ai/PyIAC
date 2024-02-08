from unittest import TestLoader, TestSuite, TextTestRunner
from PyIAC.tests.test_alarm_states import TestAlarmState
from PyIAC.tests.test_bool_alarms import TestBoolAlarms
from PyIAC.tests.test_high_alarms import TestHighAlarms
from PyIAC.tests.test_high_high_alarms import TestHighHighAlarms
from PyIAC.tests.test_low_low_alarms import TestLowLowAlarms
from PyIAC.tests.test_low_alarms import TestLowAlarms
from PyIAC.tests.test_alarm_manager import TestAlarmManager
from PyIAC.tests.test_dbmodels import TestDBModels
from PyIAC.tests.test_dbmodels_from_config_file import TestDBModelsFromConfigFile
from PyIAC.tests.test_unit_conversion import TestUnitConversion
from PyIAC.tests.test_unit_conversion_from_tags import TestUnitConversionFromTags


def suite():
    r"""
    Documentation here
    """
    tests = list()
    suite = TestSuite()
    tests.append(TestLoader().loadTestsFromTestCase(TestAlarmState))
    tests.append(TestLoader().loadTestsFromTestCase(TestBoolAlarms))
    tests.append(TestLoader().loadTestsFromTestCase(TestHighAlarms))
    tests.append(TestLoader().loadTestsFromTestCase(TestHighHighAlarms))
    tests.append(TestLoader().loadTestsFromTestCase(TestLowLowAlarms))
    tests.append(TestLoader().loadTestsFromTestCase(TestLowAlarms))
    tests.append(TestLoader().loadTestsFromTestCase(TestAlarmManager))
    tests.append(TestLoader().loadTestsFromTestCase(TestDBModels))
    tests.append(TestLoader().loadTestsFromTestCase(TestDBModelsFromConfigFile))
    tests.append(TestLoader().loadTestsFromTestCase(TestUnitConversion))
    tests.append(TestLoader().loadTestsFromTestCase(TestUnitConversionFromTags))
    suite = TestSuite(tests)
    return suite


if __name__=='__main__':
    
    runner = TextTestRunner()
    runner.run(suite())
