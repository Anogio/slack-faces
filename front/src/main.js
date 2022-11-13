import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

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
app.use(router);
app.mount("#app");

document.title = "Facedle";
