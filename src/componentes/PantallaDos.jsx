import '../App.css'

export default function PantallaDos({ imagen, onRepetir, onAnalizar }) {
  return (
    <div className='pantalla'>
      {imagen && (
        <img
          src={imagen}
          alt="Captura"
          className="imagen-capturada"
          loading="lazy"
        />
      )}

      <div className="botones">
        <button className="boton" onClick={onRepetir}>
          Repetir Imagen
        </button>
        <button className='boton_analizar' onClick={onAnalizar}>
          Analizar Imagen
        </button>
      </div>
    </div>
  );
}
