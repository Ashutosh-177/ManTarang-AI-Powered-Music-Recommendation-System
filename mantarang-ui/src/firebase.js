import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey:            "AIzaSyBl1XrQjijElFsHsuUOepj4tGUa51-iWOs",
  authDomain:        "mantarang-824ba.firebaseapp.com",
  projectId:         "mantarang-824ba",
  storageBucket:     "mantarang-824ba.firebasestorage.app",
  messagingSenderId: "869888357436",
  appId:             "1:869888357436:web:ee3ff8bd8d74a345f63f39",
};

const app      = initializeApp(firebaseConfig);
export const auth     = getAuth(app);
export const provider = new GoogleAuthProvider();
