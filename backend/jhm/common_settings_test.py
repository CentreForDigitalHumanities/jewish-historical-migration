from django.test import SimpleTestCase

import jhm.common_settings as common_settings


class CommonSettingsTest(SimpleTestCase):
    def test_does_not_define_environment_specific_settings(self):
        for name in ('DEBUG', 'SECRET_KEY', 'ALLOWED_HOSTS', 'DATABASES'):
            self.assertFalse(hasattr(common_settings, name), name)

    def test_registers_application_metadata_context_processor(self):
        processors = common_settings.TEMPLATES[0]['OPTIONS']['context_processors']
        self.assertIn('jhm.context_processors.application_metadata', processors)
