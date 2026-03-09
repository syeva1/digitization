# 08. Local Fonts Setup

## Куда класть
`assets/fonts/`

## Пример
assets/fonts/
├── BricolageGrotesque-Variable.woff2
├── SpaceGrotesk-Variable.woff2
├── Inter-Variable.woff2
├── IBMPlexMono-Regular.woff2
├── Lora-Variable.woff2
└── README.md

## Как подключать
```css
@font-face {
  font-family: "SpaceGroteskLocal";
  src: url("../assets/fonts/SpaceGrotesk-Variable.woff2") format("woff2");
  font-weight: 300 700;
  font-style: normal;
  font-display: swap;
}
```
