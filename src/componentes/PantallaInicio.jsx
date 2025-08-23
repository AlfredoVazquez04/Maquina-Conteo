import '../App.css';

export default function PantallaInicio({ onApagar, onSiguiente }) {
  return (
    <div className='pantalla'>
      <h2>Pantalla de Inicio</h2>
      <div className="botones">
        <button className="boton_apagar" onClick={onApagar}>
          Apagar
        </button>
        <button className='boton' onClick={onSiguiente}>
          Tomar Imagen
        </button>
      </div>
    </div>
  );
}
