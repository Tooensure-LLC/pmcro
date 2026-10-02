// PMCR-O layer on top of docfx's modern template (docfx 2.81.0).
// Options are the documented DocfxOptions: https://github.com/dotnet/docfx/blob/main/templates/modern/src/options.d.ts
export default {
  defaultTheme: 'auto',
  iconLinks: [
    {
      icon: 'github',
      href: 'https://github.com/Tooensure-LLC/pmcro',
      title: 'Source on GitHub'
    }
  ],
  mermaid: {
    theme: 'base',
    themeVariables: {
      primaryColor: '#1B1F4A',
      primaryTextColor: '#F5F1FF',
      primaryBorderColor: '#FF8A3D',
      lineColor: '#E0389A',
      fontFamily: 'Inter, Segoe UI, system-ui, sans-serif'
    }
  }
}
