from pyArango.connection import Connection
from pyArango.collection import Collection, Field, Edges
from pyArango import validation

conn = Connection(username="root", password="omoomo")

# db1 = conn.createDatabase(name="teste_python")

db1 = conn['teste_python']



class Usuario(Collection):
    pass


class Conexao(Edges):
    pass



if __name__ == '__main__':
    # Tutorial: https: // github.com / tariqdaouda / pyArango
    # API: http://pyarango.tariqdaouda.com/

    # col = db1.createCollection('Usuario')
    conexao = db1['Conexao']
    # a = db1['Usuario'].createDocument({'nome':'Pablo'})
    # a.save()
    # b = db1['Usuario'].createDocument({'nome':'Carol'})
    # b.save()
    pablo = db1['Usuario'].fetchByExample({'nome':'Pablo'}, batchSize=10)[0]
    carol = db1['Usuario'].fetchByExample({'nome': 'Carol'}, batchSize=10)[0]
    print(pablo)
    print(carol)
    edge = conexao.createEdge({"nome": "Casado", "data":"outubro"})
    edge.links(pablo, carol)
    edge.save()

