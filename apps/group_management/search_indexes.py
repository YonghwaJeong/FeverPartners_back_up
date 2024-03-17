from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Room

@registry.register_document
class RoomDocument(Document):
    class Index:
        name = 'rooms'

    members = fields.NestedField(properties={
        'id': fields.IntegerField(),
    })

    master = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'region': fields.TextField(),
        'region_detail': fields.TextField(),
    })

    tags = fields.NestedField(properties={
        'tag_id': fields.IntegerField(),
    })

    activityTags = fields.NestedField(properties={
        'tag_id': fields.IntegerField(),
    })

    class Django:
        model = Room
        fields = [
            'title',
            'detail',
            'favor_offline',
            'is_active',
        ]

    def prepare_members(self, instance):
        return [{'id': member.id} for member in instance.members.all()]

    def prepare_tags(self, instance):
        return [{'tag_id': tag.id} for tag in instance.tags.all()]

    def prepare_activityTags(self, instance):
        return [{'tag_id': tag.id} for tag in instance.activityTags.all()]
