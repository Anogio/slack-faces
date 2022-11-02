import { createApp } from 'vue'
import App from './App.vue'

import {
  // create naive ui
  create,
  // component
    NSelect, NSpace
} from 'naive-ui'

const naive = create({
  components: [NSelect, NSpace]
})

const app = createApp(App)
app.use(naive)
app.mount('#app')
