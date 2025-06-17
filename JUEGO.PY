import React, { useState, useEffect } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from 'firebase/auth';

// Asegúrate de que estas variables globales estén disponibles en el entorno de Canvas
const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};
const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;

// Componente principal de la aplicación
const App = () => {
    // Estados para la entrada del usuario, la respuesta de la IA, el estado de carga y Firebase
    const [prompt, setPrompt] = useState('');
    const [response, setResponse] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [db, setDb] = useState(null); // Firestore DB instance (not directly used in this AI app, but good practice for app setup)
    const [auth, setAuth] = useState(null); // Firebase Auth instance
    const [userId, setUserId] = useState(null); // User ID for authentication (useful for future database integrations)
    // Nuevo estado para la rama seleccionada
    const [selectedBranch, setSelectedBranch] = useState('general'); // Valor inicial 'general' o vacío


