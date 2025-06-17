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

    // Inicialización de Firebase y autenticación
    useEffect(() => {
        try {
            const app = initializeApp(firebaseConfig);
            const authInstance = getAuth(app);
            setAuth(authInstance);

            // Escuchar cambios en el estado de autenticación
            const unsubscribe = onAuthStateChanged(authInstance, async (user) => {
                if (user) {
                    setUserId(user.uid);
                    console.log("Usuario autenticado:", user.uid);
                } else {
                    // Si no hay token inicial, iniciar sesión anónimamente
                    if (!initialAuthToken) {
                        const anonymousUser = await signInAnonymously(authInstance);
                        setUserId(anonymousUser.user.uid);
                        console.log("Sesión anónima iniciada:", anonymousUser.user.uid);
                    } else {
                        // Usar el token inicial si está disponible
                        try {
                            const customUser = await signInWithCustomToken(authInstance, initialAuthToken);
                            setUserId(customUser.user.uid);
                            console.log("Sesión con token personalizado iniciada:", customUser.user.uid);
                        } catch (error) {
                            console.error("Error al iniciar sesión con token personalizado:", error);
                            // Fallback a inicio de sesión anónimo si el token falla
                            const anonymousUser = await signInAnonymously(authInstance);
                            setUserId(anonymousUser.user.uid);
                            console.log("Fallback a sesión anónima:", anonymousUser.user.uid);
                        }
                    }
                }
            });

            // Limpiar el listener al desmontar el componente
            return () => unsubscribe();

        } catch (error) {
            console.error("Error al inicializar Firebase:", error);
        }
    }, []); // Se ejecuta solo una vez al montar el componente

    // Función para llamar a la API de generación de texto de Gemini
    const generateText = async () => {
        setIsLoading(true);
        setResponse(''); // Limpiar la respuesta anterior

        if (!prompt.trim()) {
            setResponse('Por favor, ingresa una pregunta o un tema.');
            setIsLoading(false);
            return;
        }

        try {
            // Construir el prompt con el contexto de la rama seleccionada
            let fullPrompt = prompt;
            if (selectedBranch && selectedBranch !== 'general') {
                fullPrompt = `Considerando el contexto de la rama "${selectedBranch}": ${prompt}`;
            }

            // Historial de chat (solo un turno en este caso)
            let chatHistory = [];
            chatHistory.push({ role: "user", parts: [{ text: fullPrompt }] });

            // Payload para la API de Gemini
            const payload = { contents: chatHistory };
            const apiKey = ""; // La API key será proporcionada por el entorno de Canvas

            // URL de la API de Gemini
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

            // Realizar la llamada a la API
            const apiResponse = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await apiResponse.json();

            // Procesar la respuesta de la API
            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                const text = result.candidates[0].content.parts[0].text;
                setResponse(text);
            } else {
                setResponse('No se pudo obtener una respuesta de la IA. Inténtalo de nuevo.');
                console.error("Respuesta inesperada de la API:", result);
            }
        } catch (error) {
            setResponse('Ocurrió un error al comunicarse con la IA. Por favor, verifica tu conexión o intenta más tarde.');
            console.error("Error al llamar a la API de Gemini:", error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4 font-sans antialiased">
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                {`
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
                body {
                    font-family: 'Inter', sans-serif;
                }
                `}
            </style>

            <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-2xl border border-gray-200">
                <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">Generador de Texto con IA</h1>
                <p className="text-gray-600 mb-6 text-center">
                    Escribe tu pregunta o tema y deja que la IA te dé una respuesta, en el contexto de una rama específica.
                </p>

                {/* Selector de Rama */}
                <div className="mb-6">
                    <label htmlFor="branch-select" className="block text-gray-700 text-sm font-medium mb-2">
                        Selecciona una Rama:
                    </label>
                    <select
                        id="branch-select"
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
                        value={selectedBranch}
                        onChange={(e) => setSelectedBranch(e.target.value)}
                    >
                        <option value="general">General</option>
                        <option value="preprocesamiento">Preprocesamiento</option>
                        <option value="reconocimiento">Reconocimiento</option>
                        <option value="interfaz">Interfaz</option>
                    </select>
                </div>

                <div className="mb-6">
                    <textarea
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 resize-y min-h-[100px]"
                        placeholder="Escribe tu pregunta o tema aquí..."
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        rows="4"
                    ></textarea>
                </div>

                <button
                    onClick={generateText}
                    className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition duration-200 ease-in-out font-semibold text-lg shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                    disabled={isLoading}
                >
                    {isLoading ? (
                        <>
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Generando...
                        </>
                    ) : (
                        'Generar Respuesta'
                    )}
                </button>

                {response && (
                    <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg shadow-sm">
                        <h2 className="text-xl font-semibold text-blue-800 mb-3">Respuesta de la IA:</h2>
                        <p className="text-gray-800 whitespace-pre-wrap">{response}</p>
                    </div>
                )}

                {userId && (
                    <p className="text-xs text-gray-500 mt-6 text-center">
                        ID de Usuario: {userId}
                    </p>
                )}
            </div>
        </div>
    );
};

export default App;
