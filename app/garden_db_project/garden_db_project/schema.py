import graphene
import horticulture.schema # Import the app's schema

# This class will inherit from multiple Queries
# as we add more apps to our project
class Query(horticulture.schema.Query, graphene.ObjectType):
    # This is necessary because graphene.ObjectType is the main base class
    pass

# Define the main Mutation class inheriting from the app's Mutation
class Mutation(horticulture.schema.Mutation, graphene.ObjectType):
    # This is necessary for the same reason as Query
    pass

# Instantiate the schema with both Query and Mutation
schema = graphene.Schema(query=Query, mutation=Mutation)