import '../App.css'

export default function PantallaTres({ imagenProcesada, textoAnalisis, onVolverInicio }) {
  return (
    <div className='pantalla'>
      <h2>Resultado del análisis</h2>

      {imagenProcesada && (
        <img
          src={imagenProcesada}
          alt="Imagen Procesada"
          className="imagen-procesada"
        />
      )}

      {textoAnalisis && (
        <pre className="texto-analisis">
          {textoAnalisis}
        </pre>
      )}

      <div className="botones">
        <button className="boton" onClick={onVolverInicio}>
          Volver al inicio 
        </button>
      </div>
    </div>
  )
}