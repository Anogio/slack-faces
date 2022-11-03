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
} from "naive-ui";

const naive = create({
  components: [NSelect, NButton, NTag, NStatistic, NIcon],
});

const app = createApp(App);
app.use(naive);
app.mount("#app");
