import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { Provider } from "react-redux"
// import 
import App from './App.jsx'
import { store } from './store/store.js'
import {Toaster} from "react-hot-toast"

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Provider store={store} >

    <App />
    <Toaster position="top-right" />
    </Provider>
  </StrictMode>,
)
