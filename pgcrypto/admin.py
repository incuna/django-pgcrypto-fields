from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import object

from future import standard_library


standard_library.install_aliases()


class PGPAdmin(object):

    def get_queryset(self, request):
        """Skip any auto decryption when ORM calls are from the admin."""
        return self.model.objects.get_queryset(**{'skip_decrypt': True})
