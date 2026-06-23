import { Html, Head, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta name="description" content="SBI LifePulse - Agentic Life Event Intelligence Platform" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <body className="bg-sbi-light text-sbi-dark font-sans antialiased">
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
