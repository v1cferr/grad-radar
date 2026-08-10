import { ImageResponse } from "next/og";

/**
 * Ícone da tela inicial no iOS.
 *
 * Existe separado do icon.svg porque o `apple-touch-icon` **não aceita SVG** —
 * só jpg/jpeg/png. Sem este arquivo o iOS ignora o favicon e usa um print
 * reduzido da página, que a 180px é um borrão ilegível.
 *
 * Importa porque o uso real é no celular: o link vai por WhatsApp e é no
 * telefone que os três vão abrir e, provavelmente, fixar na tela inicial.
 * Também sem cantos arredondados de propósito — o iOS aplica a máscara dele, e
 * arredondar aqui produziria borda dupla.
 */
export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          background: "#2a78d6",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {/* O mesmo radar do icon.svg, redesenhado inline: o Satori não resolve
            <use> nem importa arquivo externo. */}
        <svg width="120" height="120" viewBox="0 0 32 32">
          <g fill="none" stroke="#ffffff" strokeWidth="2.6" strokeLinecap="round">
            <path d="M16 26.5A10.5 10.5 0 1 1 26.5 16" />
            <path d="M16 16 23.4 8.6" />
          </g>
          <circle cx="23.5" cy="22.5" r="3.1" fill="#ffffff" />
        </svg>
      </div>
    ),
    { ...size },
  );
}
