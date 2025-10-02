const { MongoClient } = require('mongodb');

class Database {
  constructor() {
    this.client = null;
    this.db = null;
    this.uri = process.env.MONGODB_URI || 'mongodb://localhost:27017';
    this.dbName = process.env.DB_NAME || 'openmanus_unified';
  }

  async connect() {
    try {
      this.client = new MongoClient(this.uri);
      await this.client.connect();
      this.db = this.client.db(this.dbName);
      console.log('Connexion à MongoDB réussie');
      return true;
    } catch (error) {
      console.error('Erreur de connexion à MongoDB:', error);
      return false;
    }
  }

  async disconnect() {
    if (this.client) {
      await this.client.close();
      console.log('Déconnexion de MongoDB');
    }
  }

  // Gestion des agents
  async createAgent(agent) {
    try {
      const collection = this.db.collection('agents');
      const result = await collection.insertOne(agent);
      return { success: true, id: result.insertedId };
    } catch (error) {
      console.error('Erreur création agent:', error);
      return { success: false, error: error.message };
    }
  }

  async getAgents() {
    try {
      const collection = this.db.collection('agents');
      const agents = await collection.find({}).toArray();
      return { success: true, agents };
    } catch (error) {
      console.error('Erreur récupération agents:', error);
      return { success: false, error: error.message };
    }
  }

  async updateAgent(id, updates) {
    try {
      const collection = this.db.collection('agents');
      const result = await collection.updateOne(
        { _id: id },
        { $set: updates }
      );
      return { success: true, modifiedCount: result.modifiedCount };
    } catch (error) {
      console.error('Erreur mise à jour agent:', error);
      return { success: false, error: error.message };
    }
  }

  async deleteAgent(id) {
    try {
      const collection = this.db.collection('agents');
      const result = await collection.deleteOne({ _id: id });
      return { success: true, deletedCount: result.deletedCount };
    } catch (error) {
      console.error('Erreur suppression agent:', error);
      return { success: false, error: error.message };
    }
  }

  // Gestion des tâches
  async createTask(task) {
    try {
      const collection = this.db.collection('tasks');
      const result = await collection.insertOne(task);
      return { success: true, id: result.insertedId };
    } catch (error) {
      console.error('Erreur création tâche:', error);
      return { success: false, error: error.message };
    }
  }

  async getTasks(agentId = null) {
    try {
      const collection = this.db.collection('tasks');
      const query = agentId ? { agentId } : {};
      const tasks = await collection.find(query).toArray();
      return { success: true, tasks };
    } catch (error) {
      console.error('Erreur récupération tâches:', error);
      return { success: false, error: error.message };
    }
  }

  // Gestion des résultats
  async saveResult(result) {
    try {
      const collection = this.db.collection('results');
      const insertResult = await collection.insertOne(result);
      return { success: true, id: insertResult.insertedId };
    } catch (error) {
      console.error('Erreur sauvegarde résultat:', error);
      return { success: false, error: error.message };
    }
  }

  async getResults(taskId = null) {
    try {
      const collection = this.db.collection('results');
      const query = taskId ? { taskId } : {};
      const results = await collection.find(query).toArray();
      return { success: true, results };
    } catch (error) {
      console.error('Erreur récupération résultats:', error);
      return { success: false, error: error.message };
    }
  }
}

module.exports = Database;

