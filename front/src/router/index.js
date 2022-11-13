import { createRouter, createWebHistory } from "vue-router";
import Main from "../components/Main.vue";
import SlackLogin from "../components/SlackLogin.vue";

const routes = [
  {
    path: "/",
    name: "Main",
    component: Main,
  },
  {
    path: "/login",
    name: "SlackLogin",
    component: SlackLogin,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
