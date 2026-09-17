import "./index.css";
import { Composition } from "remotion";
import { HelloWorld } from "./HelloWorld";
import { Logo } from "./HelloWorld/Logo";
import { FinanzasVideo } from "./templates/FinanzasVideo";
import { TerrorVideo } from "./templates/TerrorVideo";

// Each <Composition> is an entry in the sidebar!

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        // You can take the "id" to render a video:
        // npx remotion render HelloWorld
        id="HelloWorld"
        component={HelloWorld}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        // You can override these props for each render:
        // https://www.remotion.dev/docs/parametrized-rendering
        defaultProps={{
          titleText: "Welcome to Remotion",
          titleColor: "#000000",
          logoColor1: "#91EAE4",
          logoColor2: "#86A8E7",
        }}
      />

      {/* Mount any React component to make it show up in the sidebar and work on it individually! */}
      <Composition
        id="OnlyLogo"
        component={Logo}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          logoColor1: "#91dAE2",
          logoColor2: "#86A8E7",
        }}
      />

      {/* 💰 TEMPLATE 1 — Finanzas / Dinero (20 sec, 5 escenas x 4s) */}
      <Composition
        id="FinanzasVideo"
        component={FinanzasVideo}
        durationInFrames={600}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          channelName: "FINANZAS SIN MIEDO",
          scenes: [
            {
              title: "Gasta menos de lo que ganas",
              subtitle: "La regla #1 del dinero que el 90% ignora",
            },
            {
              title: "Elimina tus deudas caras",
              subtitle: "La tarjeta cobra hasta 60% de interés al año",
            },
            {
              title: "Crea un fondo de emergencia",
              subtitle: "Ahorra de 3 a 6 meses de gastos primero",
            },
            {
              title: "Invierte todos los meses",
              subtitle: "El interés compuesto premia la constancia",
            },
            {
              title: "Haz crecer tus ingresos",
              subtitle: "Ahorrar te protege. Ganar más te libera.",
            },
          ],
        }}
      />

      {/* 😱 TEMPLATE 2 — Terror / Misterio (24 sec, 3 casos x 8s) */}
      <Composition
        id="TerrorVideo"
        component={TerrorVideo}
        durationInFrames={720}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          channelName: "RELATOS DE LA NOCHE",
          footerText: "USA AURICULARES",
          scenes: [
            {
              title: "EL PUEBLO FANTASMA",
              text: "En 1987, los 300 habitantes de San Miguel abandonaron sus casas en una sola noche. Nadie sabe por qué. Las luces siguen encendidas.",
            },
            {
              title: "LA LLAMADA",
              text: "Recibió una llamada de su propio número. Al contestar, escuchó su propia voz susurrando: no contestes.",
            },
            {
              title: "ARCHIVO 13",
              text: "La cinta fue encontrada en una casa abandonada. Dura 4 minutos. Los últimos 30 segundos nadie ha podido explicarlos.",
            },
          ],
        }}
      />
    </>
  );
};
