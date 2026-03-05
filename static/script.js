document.addEventListener('DOMContentLoaded', function() {
    const questionInput = document.getElementById('questionInput');
    const askButton = document.getElementById('askButton');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsSection = document.getElementById('resultsSection');
    const answerContent = document.getElementById('answerContent');
    const sourcesContent = document.getElementById('sourcesContent');
    
    const documentInput = document.getElementById('documentInput');
    const ingestButton = document.getElementById('ingestButton');
    const ingestStatus = document.getElementById('ingestStatus');
    
    // PDF upload elements
    const pdfUpload = document.getElementById('pdfUpload');
    const pdfStatus = document.getElementById('pdfStatus');
    
    // Image upload elements
    const imageUpload = document.getElementById('imageUpload');
    const imageCaption = document.getElementById('imageCaption');
    const uploadImageBtn = document.getElementById('uploadImageBtn');
    const imageStatus = document.getElementById('imageStatus');
    let selectedImageFile = null;
    
    // Voice input elements
    const voiceButton = document.getElementById('voiceButton');
    let recognition = null;
    let isListening = false;

    // Session management
    let sessionId = localStorage.getItem('travel_session_id');
    let chatHistory = [];
    
    // Initialize Speech Recognition
    function initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onstart = function() {
                isListening = true;
                voiceButton.classList.add('listening');
                voiceButton.innerHTML = '🔴 Listening...';
                questionInput.placeholder = 'Listening... Speak now!';
            };
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                questionInput.value = transcript;
                console.log('Voice input:', transcript);
            };
            
            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);
                let errorMsg = 'Voice input error';
                
                if (event.error === 'no-speech') {
                    errorMsg = 'No speech detected. Please try again.';
                } else if (event.error === 'not-allowed') {
                    errorMsg = 'Microphone access denied. Please allow microphone access.';
                } else if (event.error === 'network') {
                    errorMsg = 'Network error. Please check your connection.';
                }
                
                alert(errorMsg);
                resetVoiceButton();
            };
            
            recognition.onend = function() {
                resetVoiceButton();
            };
            
            return true;
        } else {
            console.warn('Speech recognition not supported');
            return false;
        }
    }
    
    function resetVoiceButton() {
        isListening = false;
        voiceButton.classList.remove('listening');
        voiceButton.innerHTML = '🎤 Voice';
        questionInput.placeholder = 'Ask me anything about travel destinations...';
    }
    
    // Voice button click handler
    voiceButton.addEventListener('click', function() {
        if (!recognition) {
            if (!initSpeechRecognition()) {
                alert('Voice input is not supported in your browser. Please use Chrome, Edge, or Safari.');
                return;
            }
        }
        
        if (isListening) {
            recognition.stop();
            resetVoiceButton();
        } else {
            try {
                recognition.start();
            } catch (error) {
                console.error('Failed to start recognition:', error);
                alert('Failed to start voice input. Please try again.');
                resetVoiceButton();
            }
        }
    });
    
    // Initialize on page load
    initSpeechRecognition();
    
    // PDF upload handling
    pdfUpload.addEventListener('change', async function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        console.log('PDF selected:', file.name, 'Size:', file.size);
        
        // Check file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            showPdfStatus('PDF too large. Please upload a file smaller than 10MB.', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        showPdfStatus('📄 Uploading and processing PDF...', 'info');
        
        try {
            console.log('Sending PDF to /upload_pdf...');
            
            const response = await fetch('/upload_pdf', {
                method: 'POST',
                body: formData
            });
            
            console.log('Response status:', response.status);
            
            const data = await response.json();
            console.log('Response data:', data);
            
            if (response.ok) {
                showPdfStatus(
                    `✅ ${file.name} uploaded! ${data.chunks_created} chunks created from ${data.pages} pages.`,
                    'success'
                );
                pdfUpload.value = ''; // Clear input
            } else {
                showPdfStatus(`❌ Error: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('PDF upload error:', error);
            showPdfStatus(`❌ Error: ${error.message}`, 'error');
        }
    });
    
    function showPdfStatus(message, type) {
        pdfStatus.textContent = message;
        pdfStatus.className = `status-message ${type}`;
        pdfStatus.classList.remove('hidden');
        
        if (type === 'success') {
            setTimeout(() => {
                pdfStatus.classList.add('hidden');
            }, 5000);
        }
    }

    // Image upload handling
    imageUpload.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        console.log('Image selected:', file.name, 'Size:', file.size);
        
        // Check file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            showImageStatus('Image too large. Please upload a file smaller than 5MB.', 'error');
            return;
        }
        
        // Store file and show caption input
        selectedImageFile = file;
        imageCaption.classList.remove('hidden');
        uploadImageBtn.classList.remove('hidden');
        imageCaption.focus();
        showImageStatus('📝 Please describe the image before uploading', 'info');
    });
    
    uploadImageBtn.addEventListener('click', async function() {
        if (!selectedImageFile) {
            showImageStatus('Please select an image first', 'error');
            return;
        }
        
        const caption = imageCaption.value.trim();
        if (!caption) {
            showImageStatus('Please provide a description for the image', 'error');
            imageCaption.focus();
            return;
        }
        
        const formData = new FormData();
        formData.append('file', selectedImageFile);
        formData.append('caption', caption);
        
        showImageStatus('🖼️ Uploading image...', 'info');
        uploadImageBtn.disabled = true;
        
        try {
            console.log('Sending image to /upload_image with caption:', caption);
            
            const response = await fetch('/upload_image', {
                method: 'POST',
                body: formData
            });
            
            console.log('Response status:', response.status);
            
            const data = await response.json();
            console.log('Response data:', data);
            
            if (response.ok) {
                showImageStatus(
                    `✅ ${selectedImageFile.name} uploaded! ${data.chunks_created} chunks created. You can now query about this image.`,
                    'success'
                );
                // Reset
                imageUpload.value = '';
                imageCaption.value = '';
                imageCaption.classList.add('hidden');
                uploadImageBtn.classList.add('hidden');
                selectedImageFile = null;
            } else {
                showImageStatus(`❌ Error: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Image upload error:', error);
            showImageStatus(`❌ Error: ${error.message}`, 'error');
        } finally {
            uploadImageBtn.disabled = false;
        }
    });
    
    function showImageStatus(message, type) {
        imageStatus.textContent = message;
        imageStatus.className = `status-message ${type}`;
        imageStatus.classList.remove('hidden');
        
        if (type === 'success') {
            setTimeout(() => {
                imageStatus.classList.add('hidden');
            }, 5000);
        }
    }

    askButton.addEventListener('click', async function() {
        const question = questionInput.value.trim();
        
        if (!question) {
            alert('Please enter a question');
            return;
        }

        // Add user message to chat history display
        addMessageToChat('user', question);
        questionInput.value = '';

        resultsSection.classList.add('hidden');
        loadingIndicator.classList.remove('hidden');
        askButton.disabled = true;

        try {
            const requestBody = { 
                question: question,
                session_id: sessionId
            };
            
            console.log('Sending request to /query...');
            
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });
            
            console.log('Response status:', response.status);

            const data = await response.json();
            console.log('Response data:', data);

            if (response.ok) {
                // Save session ID
                if (data.session_id) {
                    sessionId = data.session_id;
                    localStorage.setItem('travel_session_id', sessionId);
                }

                // Add assistant message to chat history display
                addMessageToChat('assistant', data.answer);

                displayResults(data);
            } else {
                throw new Error(data.error || 'Failed to get answer');
            }
        } catch (error) {
            console.error('Fetch error:', error);
            addMessageToChat('error', `Error: ${error.message}`);
        } finally {
            loadingIndicator.classList.add('hidden');
            askButton.disabled = false;
        }
    });

    questionInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            askButton.click();
        }
    });

    function addMessageToChat(role, content) {
        chatHistory.push({ role, content });
        
        // Keep only last 10 messages in display
        if (chatHistory.length > 10) {
            chatHistory = chatHistory.slice(-10);
        }
        
        renderChatHistory();
    }

    function renderChatHistory() {
        const chatContainer = document.getElementById('chatHistory');
        if (!chatContainer) return;

        chatContainer.innerHTML = chatHistory.map(msg => {
            const className = msg.role === 'user' ? 'user-message' : 
                            msg.role === 'assistant' ? 'assistant-message' : 'error-message';
            return `<div class="chat-message ${className}">${msg.content}</div>`;
        }).join('');

        // Auto scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function displayResults(data) {
        answerContent.innerHTML = `<p>${data.answer}</p>`;
        
        if (data.retrieved_sources && data.retrieved_sources.length > 0) {
            sourcesContent.innerHTML = data.retrieved_sources.map((source, index) => `
                <div class="source-item">
                    <div class="source-header">
                        <span class="source-title">${source.metadata.source_title} (Chunk ${source.metadata.chunk_id})</span>
                        <span class="source-score">Score: ${source.score.toFixed(4)}</span>
                    </div>
                    <p class="source-text">${source.text}</p>
                </div>
            `).join('');
        } else {
            sourcesContent.innerHTML = '<p>No sources found</p>';
        }

        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    ingestButton.addEventListener('click', async function() {
        const text = documentInput.value.trim();
        
        if (!text) {
            showStatus('Please enter documents to add', 'error');
            return;
        }

        const documents = text.split('\n').filter(line => line.trim());
        
        if (documents.length === 0) {
            showStatus('No valid documents found', 'error');
            return;
        }

        ingestButton.disabled = true;
        ingestStatus.classList.add('hidden');

        try {
            const response = await fetch('/ingest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ documents: documents })
            });

            const data = await response.json();

            if (response.ok) {
                showStatus(`Successfully added ${data.documents_ingested} documents (${data.chunks_created} chunks created)!`, 'success');
                documentInput.value = '';
            } else {
                throw new Error(data.error || 'Failed to ingest documents');
            }
        } catch (error) {
            showStatus(`Error: ${error.message}`, 'error');
        } finally {
            ingestButton.disabled = false;
        }
    });

    function showStatus(message, type) {
        ingestStatus.textContent = message;
        ingestStatus.className = `status-message ${type}`;
        ingestStatus.classList.remove('hidden');
        
        setTimeout(() => {
            ingestStatus.classList.add('hidden');
        }, 5000);
    }

    // Clear session button (optional)
    window.clearSession = async function() {
        if (sessionId) {
            await fetch('/clear_session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });
        }
        localStorage.removeItem('travel_session_id');
        sessionId = null;
        chatHistory = [];
        renderChatHistory();
        alert('Conversation cleared!');
    };
});
