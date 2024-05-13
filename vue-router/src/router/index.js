import { createWebHistory, createRouter } from "vue-router";
import Key from "@/views/KeyWordSeek.vue";
import Img from "@/views/ImgSeek.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: Key,
  },
  {
    path: "/search",
    name: "Search",
    component: Img,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;