/**
 * Firebase configuration and initialization
 * Handles authentication ONLY (no Firestore)
 */

import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

// Firebase configuration from environment variables
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY ?? "",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN ?? "",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID ?? "",
};

// Validate configuration
const isConfigValid = Boolean(
  firebaseConfig.apiKey &&
  firebaseConfig.authDomain &&
  firebaseConfig.projectId
);

if (!isConfigValid) {
  console.error('❌ Firebase configuration is missing or invalid. Skipping Firebase initialization.');
  console.error('Please create a .env file with:');
  console.error('VITE_FIREBASE_API_KEY=...');
  console.error('VITE_FIREBASE_AUTH_DOMAIN=...');
  console.error('VITE_FIREBASE_PROJECT_ID=...');
}

// Initialize Firebase only when configuration is valid
let app;
let auth;
let googleProvider;

if (isConfigValid) {
  app = initializeApp(firebaseConfig);
  auth = getAuth(app);
  googleProvider = new GoogleAuthProvider();
  // Configure Google provider
  googleProvider.setCustomParameters({ prompt: 'select_account' });
}

export { auth, googleProvider };
export default app;
