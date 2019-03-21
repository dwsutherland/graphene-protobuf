#!/usr/bin/env python

import json
import graphene
from collections import OrderedDict
from graphene.types.resolver import dict_resolver, attr_resolver
from graphene.types.generic import GenericScalar
from google.protobuf.json_format import MessageToDict
import hello_pb2

def dict_or_attr_resolver(attname, default_value, root, info, **args):
    resolver = attr_resolver
    if isinstance(root, dict):
        resolver = dict_resolver
    return resolver(attname, default_value, root, info, **args)

class Episode(graphene.Enum):
    NEWHOPE = 4
    EMPIRE = 5
    JEDI = 6

    @property
    def description(self):
        if self == Episode.NEWHOPE:
            return 'New Hope Episode'
        return 'Other episode'

class Starship(graphene.ObjectType):
    name = graphene.String()
    length = graphene.Int()

class Character(graphene.Interface):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)
    friends = graphene.List(lambda: Character)
    type = graphene.String()

    @classmethod
    def resolve_type(cls, instance, info):
        if instance.type == 'DROID':
            return Droid
        return Human

class Human(graphene.ObjectType):
    class Meta:
        interfaces = (Character, )

    starships = graphene.List(Starship)
    home_planet = graphene.String()


class Droid(graphene.ObjectType):
    class Meta:
        interfaces = (Character, )

    primary_function = graphene.String()

class SearchResult(graphene.Union):
    class Meta:
        types = (Human, Droid, Starship)


class CreatePerson(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    ok = graphene.Boolean()
    person = graphene.Field(lambda: Person)

    def mutate(self, info, name):
        person = hello_pb2.Person()
        person.name = name
        person.details['item1'] = "some string1"
        person.details['item2'] = "some string2"
        person.details['item3'] = "some string3"
        print(OrderedDict(person.details))
        for key, val in person.details.items():
            print(key, val)
        ok = True
        return CreatePerson(person=MessageToDict(person,
                including_default_value_fields=True), ok=ok)

class Person(graphene.ObjectType):
    class Meta:
        default_resolver = dict_resolver
    name = graphene.String()
    age = graphene.Int()
    details = graphene.Field(GenericScalar)

class MyMutations(graphene.ObjectType):
    create_person = CreatePerson.Field()

class Query(graphene.ObjectType):
    person = graphene.Field(Person)
    hello = graphene.String(name=graphene.String(default_value="stranger"))
    hero = graphene.Field(
        Character,
        required=True,
        episode=graphene.Int(required=True)
    )


    def resolve_hello(self, info, name):
        return 'Hello ' + name

    def resolve_hero(_, info, episode):
        # Luke is the hero of Episode V
        if episode == 5:
            return hello_pb2.Human(name='Luke Skywalker')
        return hello_pb2.Droid(name='R2-D2', type='DROID')

schema = graphene.Schema(query=Query, mutation=MyMutations, types=[Human, Droid])

if __name__ == '__main__':
    #print(get_human(name='Luke Skywalker'))
    result = schema.execute("""{ hello }""")
    result2 = schema.execute("""query HeroForEpisode($episode: Int = 5){
        hero(episode: $episode){
            __typename
            name
            ... on Droid{
                primaryFunction
            }
            ... on Human{
                homePlanet
            }
        }
    }
""", variable_values={'episode': 4})
    result3 =  schema.execute("""mutation myFirstMutation{
        createPerson(name:"Peter") {
            person{
                name
                details
            }
            ok
        }
    }
""")
    print(result.data['hello'])
    print(json.dumps(result2.data))
    print(json.dumps(result2.errors))
    print(dict(result3.data))
    print(json.dumps(result3.data))
    print(json.dumps(result3.errors))

