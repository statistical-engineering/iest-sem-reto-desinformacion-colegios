/**
 * Worker del reto en Cloudflare (ADR-W3). Las páginas de web/ las sirve Cloudflare como recursos
 * estáticos sin pasar por aquí; este archivo recibe todo /api/* y lo que no es un archivo de web/.
 * No hace lógica (U1-P3): pasa /api/* al único Durable Object «Reto» y responde 404 a lo demás.
 * Si el objeto no responde, contesta 503 (contrato C1, Q4-A).
 */
import { respuesta_json } from "./reto.js";

export { Reto } from "./reto.js";

export default {
  /**
   * @param {Request} peticion
   * @param {{RETO: DurableObjectNamespace}} env
   * @returns {Promise<Response>}
   */
  async fetch(peticion, env) {
    if (!new URL(peticion.url).pathname.startsWith("/api/")) return respuesta_json(404, { error: "No encontrado." });
    try {
      return await env.RETO.get(env.RETO.idFromName("servicio")).fetch(peticion);
    } catch (error) {
      console.error("El Durable Object no respondió:", error instanceof Error ? error.message : String(error));
      return respuesta_json(503, { error: "El servicio no responde. Intenta de nuevo en un momento." });
    }
  },
};
