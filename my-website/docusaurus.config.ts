import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'AI Diven Physical AI & Humanoid Robotics',
  tagline: 'A Comprehensive Guide to Physical AI & Humanoid Robotics',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://asif-abdulqadir.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/text-book-hackathon/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'asif-abdulqadir', // Usually your GitHub org/user name.
  projectName: 'text-book-hackathon', // Usually your repo name.

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // Change this to your repo.
          editUrl:
            'https://github.com/asif-abdulqadir/text-book-hackathon/edit/main/',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Change this to your repo.
          editUrl:
            'https://github.com/asif-abdulqadir/text-book-hackathon/edit/main/',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    // [
    //   'docusaurus-pdf',
    //   {
    //     // Options for the docusaurus-pdf plugin
    //     debug: false, // Set to true for debugging
    //     paperSize: 'A4', // Or other sizes like 'letter', 'legal', etc.
    //     printBackground: true,
    //     // Include all docs in the PDF
    //     docs: {
    //       path: './docs',
    //       // Optionally specify specific doc IDs to include
    //       // ids: ['module1-ros2/introduction', 'module2-gazebo/simulation', ...],
    //     },
    //     // Optionally specify blog path if you want to include blogs
    //     // blog: {
    //     //   path: './blog',
    //     // },
    //     // Output directory (relative to build directory)
    //     outputDir: 'pdf',
    //     // Output filename
    //     outputFile: 'ai-diven-book.pdf',
    //   }
    // ],
  ],




  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    // Expose environment variables to client-side code
    customFields: {
      NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
    },
    navbar: {
      title: 'AI Diven Physical AI & Humanoid Robotics Book',
      logo: {
        alt: 'Physical AI & Humanoid Robotics Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Book Chapters',
        },
        {to: '/blog', label: 'Research Blog', position: 'left'},
        {
          href: 'https://github.com/asif-abdulqadir/text-book-hackathon',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Book Content',
          items: [
            {
              label: 'Introduction',
              to: '/docs/intro',
            },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'AI Research',
              href: 'https://ai.google/research/',
            },
            {
              label: 'Robotics Research',
              href: 'https://www.ieee-ras.org/',
            },
            {
              label: 'Physical AI Resources',
              href: 'https://www.computer.org/',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Research Blog',
              to: '/blog',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/asif-abdulqadir/text-book-hackathon',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Muhammad Asif. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
