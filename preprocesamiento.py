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
