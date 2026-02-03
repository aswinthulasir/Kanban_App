// API Client
const API_BASE_URL = '/api/v1';

class APIClient {
  constructor() {
    this.token = localStorage.getItem('access_token');
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (response.status === 401) {
        // Unauthorized - redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return;
      }

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Request failed');
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return null;
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Auth endpoints
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(username, password) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    this.token = data.access_token;
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return data;
  }

  logout() {
    this.token = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  }

  // User endpoints
  async getCurrentUser() {
    return this.request('/users/me');
  }

  // Board endpoints
  async getBoards() {
    return this.request('/boards/');
  }

  async getBoard(boardId) {
    return this.request(`/boards/${boardId}`);
  }

  async createBoard(boardData) {
    return this.request('/boards/', {
      method: 'POST',
      body: JSON.stringify(boardData),
    });
  }

  async updateBoard(boardId, boardData) {
    return this.request(`/boards/${boardId}`, {
      method: 'PUT',
      body: JSON.stringify(boardData),
    });
  }

  async deleteBoard(boardId) {
    return this.request(`/boards/${boardId}`, {
      method: 'DELETE',
    });
  }

  // Column endpoints
  async getBoardColumns(boardId) {
    return this.request(`/columns/board/${boardId}`);
  }

  async createColumn(columnData) {
    return this.request('/columns/', {
      method: 'POST',
      body: JSON.stringify(columnData),
    });
  }

  async updateColumn(columnId, columnData) {
    return this.request(`/columns/${columnId}`, {
      method: 'PUT',
      body: JSON.stringify(columnData),
    });
  }

  async deleteColumn(columnId) {
    return this.request(`/columns/${columnId}`, {
      method: 'DELETE',
    });
  }

  // Task endpoints
  async getTasks(boardId) {
    return this.request(`/tasks/?board_id=${boardId}`);
  }

  async getTask(taskId) {
    return this.request(`/tasks/${taskId}`);
  }

  async createTask(taskData) {
    return this.request('/tasks/', {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async updateTask(taskId, taskData) {
    return this.request(`/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
  }

  async deleteTask(taskId) {
    return this.request(`/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async searchTasks(query, boardId = null) {
    const params = new URLSearchParams({ q: query });
    if (boardId) {
      params.append('board_id', boardId);
    }
    return this.request(`/tasks/search?${params}`);
  }

  // Comment endpoints
  async getTaskComments(taskId) {
    return this.request(`/comments/task/${taskId}`);
  }

  async createComment(commentData) {
    return this.request('/comments/', {
      method: 'POST',
      body: JSON.stringify(commentData),
    });
  }

  async updateComment(commentId, commentData) {
    return this.request(`/comments/${commentId}`, {
      method: 'PUT',
      body: JSON.stringify(commentData),
    });
  }

  async deleteComment(commentId) {
    return this.request(`/comments/${commentId}`, {
      method: 'DELETE',
    });
  }
}

// Export singleton instance
const api = new APIClient();
