<template>
    <div class="tasks_container">
        <div class="tasks-header">
            <input 
                v-model="newTask"
                type="text"
                placeholder="Введите задачу..."
                class="task-input"
                @keyup.enter="createTask"
            />
            <button @click="createTask" class="add-button">+</button>
        </div>

        <div class="tasks-list">
            <div
                v-for="task in tasks"
                :key="task.id"
                class="task-item"
            >
                <div class="task-text">
                    {{ task.title }}
                </div>
                <button
                    class="complete-button"
                    @click="completeTask(task.id)">Выполнено
                </button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'TasksView',
    data() {
        return {
            tasks: [],
            newTask: ''
        }
    },
    async mounted() {
        await this.fetchTasks()
    },
    methods: {
        async fetchTasks() {
            try {
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user
                const response = await fetch(`https://refactored-fishstick-jj7qgwww9x94cq4r6-8000.app.github.dev/api/tasks/${tg_user.id}`)
                const data = await response.json()
                this.tasks = data
            } catch (error) {
                console.log('error', error)
            }
        },
        async createTask() {
            if (!this.newTask) return

            try {
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user
                const response = await fetch(`https://refactored-fishstick-jj7qgwww9x94cq4r6-8000.app.github.dev/api/add`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ tg_id: tg_user.id, title: this.newTask })
                })
                if (response.ok) {
                    this.newTask = ''
                    await this.fetchTasks()
                } else {
                    console.error('Ошибка', response.status)
                }
            } catch (eror) {
                console.log('Ошибка', error)
            }
        },
        async completeTask(taskId) {
            try {
                const response = await fetch(`https://refactored-fishstick-jj7qgwww9x94cq4r6-8000.app.github.dev/api/completed`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ id: taskId })
                })
                if (response.ok) {
                    await this.fetchTasks()
                } else {
                    console.error('Ошибка', response.status)
                }
            } catch (eror) {
                console.log('Ошибка', error)
            }
        }
    }
}
</script>

<style scoped>
.tasks-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow-y: auto; /* Прокрутка, если задач много */
}

.tasks-header {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  margin-bottom: 16px;
}

.task-input {
  flex: 1;
  padding: 8px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 8px;
  margin-right: 8px;
}

.add-button {
  background-color: #007aff; /* Цвет в стиле iOS */
  color: white;
  border: none;
  padding: 0 16px;
  font-size: 24px;
  border-radius: 50%;
  cursor: pointer;
  outline: none;
  height: 40px;
  width: 40px;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #ffffffcc;
  padding: 8px 12px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.task-text {
  font-size: 16px;
}

.complete-button {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
}
</style>
  