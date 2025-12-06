/**
 * @fileoverview Utility functions for handling APA style citations.
 */

type CitationType = 'book' | 'article' | 'website' | 'other';

interface BaseCitation {
  id: string;
  authors: string[];
  year: number;
  title: string;
  url?: string;
  accessDate?: string;
}

interface BookCitation extends BaseCitation {
  type: 'book';
  publisher: string;
}

interface ArticleCitation extends BaseCitation {
  type: 'article';
  journal: string;
  volume?: number;
  issue?: number;
  pages?: string;
  doi?: string;
}

interface WebsiteCitation extends BaseCitation {
  type: 'website';
  siteName?: string;
}

interface OtherCitation extends BaseCitation {
  type: 'other';
  description?: string; // For custom descriptions if other fields don't fit
}

export type Citation = BookCitation | ArticleCitation | WebsiteCitation | OtherCitation;

/**
 * Formats authors for APA style.
 * Supports up to 2 authors: "Author A & Author B".
 * For 3+ authors: "Author A et al."
 */
function formatAuthors(authors: string[]): string {
  if (authors.length === 0) return 'N.D.'; // No Date
  if (authors.length === 1) return authors[0];
  if (authors.length === 2) return `${authors[0]} & ${authors[1]}`;
  return `${authors[0]} et al.`;
}

/**
 * Formats an in-text citation according to APA 7th edition style.
 * @param citation The citation object.
 * @returns The formatted in-text citation string (e.g., "(Author, Year)" or "(Author1 & Author2, Year)").
 */
export function formatInTextCitation(citation: Citation): string {
  const authorString = formatAuthors(citation.authors);
  return `(${authorString}, ${citation.year})`;
}

/**
 * Formats a full reference entry according to APA 7th edition style.
 * This is a more comprehensive example supporting various types.
 * @param citation The citation object.
 * @returns The formatted full reference string.
 */
export function formatReference(citation: Citation): string {
  const authorString = formatAuthors(citation.authors);
  let reference = `${authorString} (${citation.year}).`;

  switch (citation.type) {
    case 'book':
      reference += ` *${citation.title}*. ${citation.publisher}.`;
      break;
    case 'article':
      reference += ` ${citation.title}. *${citation.journal}*`;
      if (citation.volume) {
        reference += `, *${citation.volume}*`;
        if (citation.issue) {
          reference += `(${citation.issue})`;
        }
      }
      if (citation.pages) {
        reference += `, ${citation.pages}.`;
      } else {
        reference += '.';
      }
      if (citation.doi) {
        reference += ` ${citation.doi}`;
      }
      break;
    case 'website':
      reference += ` ${citation.title}.`;
      if (citation.siteName) {
        reference += ` ${citation.siteName}.`;
      }
      if (citation.url) {
        reference += ` Retrieved from ${citation.url}`;
      }
      if (citation.accessDate) {
        reference += ` (Accessed ${citation.accessDate})`;
      }
      reference += '.';
      break;
    case 'other':
      reference += ` ${citation.title}.`;
      if (citation.description) {
        reference += ` ${citation.description}.`;
      }
      if (citation.url) {
        reference += ` Retrieved from ${citation.url}`;
      }
      if (citation.accessDate) {
        reference += ` (Accessed ${citation.accessDate})`;
      }
      reference += '.';
      break;
    default:
      reference += ` ${citation.title}. ${citation.url ? `Retrieved from ${citation.url}.` : ''}`;
  }
  return reference;
}

/**
 * Example usage with expanded citation types:
 */
const exampleBook: Citation = {
  id: 'ros2-book',
  type: 'book',
  authors: ['Robot Operating System Team'],
  year: 2023,
  title: 'ROS 2 Documentation: The Definitive Guide',
  publisher: 'ROS Publishers',
  url: 'https://docs.ros.org/en/iron/'
};

const exampleArticle: Citation = {
  id: 'humanoid-control',
  type: 'article',
  authors: ['Smith, J.', 'Doe, A.'],
  year: 2022,
  title: 'Advanced Control Strategies for Bipedal Humanoid Robots',
  journal: 'Journal of Robotics Research',
  volume: 15,
  issue: 3,
  pages: '123-145',
  doi: '10.xxxx/yyyy'
};

const exampleWebsite: Citation = {
  id: 'ai-news',
  type: 'website',
  authors: ['OpenAI'],
  year: 2024,
  title: 'Latest Developments in Large Language Models',
  siteName: 'OpenAI Blog',
  url: 'https://openai.com/blog/latest-llm-developments',
  accessDate: 'December 5, 2025'
};

console.log('In-text citation (Book):', formatInTextCitation(exampleBook));
console.log('Reference (Book):', formatReference(exampleBook));
console.log('\nIn-text citation (Article):', formatInTextCitation(exampleArticle));
console.log('Reference (Article):', formatReference(exampleArticle));
console.log('\nIn-text citation (Website):', formatInTextCitation(exampleWebsite));
console.log('Reference (Website):', formatReference(exampleWebsite));

