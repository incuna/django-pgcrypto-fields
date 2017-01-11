class PGPAdmin(object):

    def get_queryset(self, request):
        """Skip any auto decryption when ORM calls are from the admin."""
        return self.model.objects.get_queryset(**{'skip_decrypt': True})
