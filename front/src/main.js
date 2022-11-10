import { createApp } from "vue";
import App from "./App.vue";

import {
  // create naive ui
  create,
  // component
  NSelect,
  NButton,
  NTag,
  NStatistic,
  NIcon,
  NAlert,
} from "naive-ui";

const naive = create({
  components: [NSelect, NButton, NTag, NStatistic, NIcon, NAlert],
});

const app = createApp(App);
app.use(naive);
app.mount("#app");

document.title = "Facedle";
