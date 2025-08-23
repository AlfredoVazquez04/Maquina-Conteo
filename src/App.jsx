// App.jsx
import { useState } from 'react';
import './App.css';
import PantallaInicio from './componentes/PantallaInicio';
import PantallaDos from './componentes/PantallaDos';
import PantallaTres from './componentes/PantallaTres';

function App() {
  const [pantalla, setPantalla] = useState("inicio");
  const [imagen, setImagen] = useState(null);
  const [imagenProcesada, setImagenProcesada] = useState(null);
  const [textoAnalisis, setTextoAnalisis] = useState(null);

  // Capturar imagen y mostrarla
  const tomarImagen = async () => {
    await fetch("http://localhost:8000/tomar-imagen");
    const res = await fetch("http://localhost:8000/obtener-imagen");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    setImagen(url);
    setPantalla("pantalla2");
  };

  // Analizar imagen y mostrar resultado
  const analizarImg = async () => {
    const res = await fetch("http://localhost:8000/analizar-imagen");
    const data = await res.json();

    if (data.error) {
      alert(data.error);
      return;
    }

    const imagenBase64 = "data:image/jpeg;base64," + data.imagen_procesada;
    setImagenProcesada(imagenBase64);
    setTextoAnalisis(data.texto.mensaje);

    setPantalla("final");
  };

  return (
    <div>
      {pantalla === "inicio" && (
        <PantallaInicio
          onSiguiente={tomarImagen}
          onApagar={() => setPantalla("final")}
        />
      )}

      {pantalla === "pantalla2" && (
        <PantallaDos
          imagen={imagen}
          onRepetir={tomarImagen}
          onAnalizar={analizarImg}
        />
      )}

      {pantalla === "final" && (
        <PantallaTres
          imagenProcesada={imagenProcesada}
          textoAnalisis={textoAnalisis}
          onVolverInicio={() => setPantalla("inicio")}
        />
      )}
    </div>
  );
}

export default App;
