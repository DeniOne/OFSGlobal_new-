import React from 'react';
import ReactDOM from 'react-dom/client';
import { ConfigProvider } from 'antd';
import App from './App';
import { antdTheme } from './theme';
import './styles/App.css';
import './index.css';
import { AuthProvider } from './hooks/useAuth';
import { BrowserRouter as Router } from 'react-router-dom';
import 'antd/dist/reset.css';

// Импорт дополнительных стилей для скроллбаров в dark mode
import './styles/dark-theme.css';
// Импорт глобальных стилей для исправления проблем с фантомами
import './styles/global.css';
// Импорт радикального решения для удаления всех фантомов
import './styles/table-fix.css';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <ConfigProvider theme={antdTheme}>
      <Router>
        <AuthProvider>
          <App />
        </AuthProvider>
      </Router>
    </ConfigProvider>
  </React.StrictMode>,
);