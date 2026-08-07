import { createApp } from 'vue';
import App from './App.vue';

const app = createApp(App);
app.mount('#app');

Note: Ensure you have a `main.ts` file in your project root, which imports the Vue application and mounts it to the DOM.