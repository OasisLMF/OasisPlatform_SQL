from rest_framework import serializers

from django.contrib.sites.shortcuts import get_current_site

from .models import Portfolio


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = (
            'name',
            'id',
            'created',
            'modified',
            'reinsurance_info_file',
        )

    def create(self, validated_data):
        data = dict(validated_data)
        if not data.get('creator') and 'request' in self.context:
            data['creator'] = self.context.get('request').user
        return super(PortfolioSerializer, self).create(data)

    def to_representation(self, instance):
        rep = super(PortfolioSerializer, self).to_representation(instance)
        rep['accounts_file'] = instance.get_absolute_accounts_file_url()
        rep['location_file'] = instance.get_absolute_location_file_url()
        rep['reinsurance_info_file'] = instance.get_absolute_reinsurance_info_file_url()
        rep['reinsurance_source_file'] = instance.get_absolute_reinsurance_source_file_url()

        if self.context.get('request'):
            rep['accounts_file'] = self.context['request'].build_absolute_uri(rep['accounts_file'])
            rep['location_file'] = self.context['request'].build_absolute_uri(rep['location_file'])
            rep['reinsurance_info_file'] = self.context['request'].build_absolute_uri(rep['reinsurance_info_file'])
            rep['reinsurance_source_file'] = self.context['request'].build_absolute_uri(rep['reinsurance_source_file'])

        return rep