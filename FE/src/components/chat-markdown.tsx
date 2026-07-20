"use client";

/**
 * Render markdown nhẹ cho tin nhắn AI (bold, bullet, đánh số, citation link).
 *
 * AI trả về markdown đơn giản: `**đậm**`, `- bullet`, `1. danh sách`,
 * `[1](/phan-khu/slug)` — trước đây hiển thị thô rất khó đọc. Renderer này
 * không dùng dangerouslySetInnerHTML nên an toàn với nội dung từ LLM.
 */

import { ReactNode } from "react";

function safeLinkUrl(url: string): string | null {
  if (url.startsWith("/") && !url.startsWith("//")) return url;
  try {
    const parsed = new URL(url);
    return parsed.protocol === "https:" ? parsed.href : null;
  } catch {
    return null;
  }
}

// Tách inline: **bold** và [label](url)
function renderInline(text: string, keyPrefix: string, linkClass: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  const pattern = /(\*\*[^*]+\*\*)|(\[[^\]]+\]\([^)]+\))/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let index = 0;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      nodes.push(text.slice(lastIndex, match.index));
    }
    const token = match[0];
    if (token.startsWith("**")) {
      nodes.push(<strong key={`${keyPrefix}-b${index}`}>{token.slice(2, -2)}</strong>);
    } else {
      const linkMatch = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(token);
      if (linkMatch) {
        const [, label, url] = linkMatch;
        const safeUrl = safeLinkUrl(url);
        if (safeUrl) {
          const isInternal = safeUrl.startsWith("/");
          nodes.push(
            <a
              className={linkClass}
              href={safeUrl}
              key={`${keyPrefix}-a${index}`}
              rel={isInternal ? undefined : "noopener noreferrer"}
              target={isInternal ? undefined : "_blank"}
            >
              {label}
            </a>
          );
        } else {
          nodes.push(<span key={`${keyPrefix}-a${index}`}>{label}</span>);
        }
      } else {
        nodes.push(token);
      }
    }
    lastIndex = match.index + token.length;
    index += 1;
  }
  if (lastIndex < text.length) {
    nodes.push(text.slice(lastIndex));
  }
  return nodes;
}

type Block =
  | { type: "paragraph"; lines: string[] }
  | { type: "bullets"; items: string[] }
  | { type: "numbered"; items: string[] };

function parseBlocks(content: string): Block[] {
  const blocks: Block[] = [];
  for (const rawLine of content.replace(/\r\n/g, "\n").split("\n")) {
    const line = rawLine.trim();
    if (!line) {
      blocks.push({ type: "paragraph", lines: [] });
      continue;
    }
    const bulletMatch = /^[-•*]\s+(.*)$/.exec(line);
    const numberedMatch = /^(\d+)[.)]\s+(.*)$/.exec(line);
    const last = blocks[blocks.length - 1];
    if (bulletMatch) {
      if (last?.type === "bullets") last.items.push(bulletMatch[1]);
      else blocks.push({ type: "bullets", items: [bulletMatch[1]] });
    } else if (numberedMatch) {
      if (last?.type === "numbered") last.items.push(numberedMatch[2]);
      else blocks.push({ type: "numbered", items: [numberedMatch[2]] });
    } else if (last?.type === "paragraph") {
      last.lines.push(line);
    } else {
      blocks.push({ type: "paragraph", lines: [line] });
    }
  }
  return blocks.filter((b) => (b.type === "paragraph" ? b.lines.length > 0 : b.items.length > 0));
}

export function ChatMarkdown({
  content,
  linkClass = "font-semibold text-cyan-600 underline underline-offset-2 hover:text-cyan-500",
}: {
  content: string;
  linkClass?: string;
}) {
  const blocks = parseBlocks(content);

  return (
    <div className="space-y-2 text-sm leading-relaxed">
      {blocks.map((block, blockIndex) => {
        if (block.type === "bullets") {
          return (
            <ul className="ml-1 list-none space-y-1" key={blockIndex}>
              {block.items.map((item, itemIndex) => (
                <li className="flex gap-2" key={itemIndex}>
                  <span className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full bg-current opacity-50" />
                  <span>{renderInline(item, `${blockIndex}-${itemIndex}`, linkClass)}</span>
                </li>
              ))}
            </ul>
          );
        }
        if (block.type === "numbered") {
          return (
            <ol className="ml-1 space-y-1" key={blockIndex}>
              {block.items.map((item, itemIndex) => (
                <li className="flex gap-2" key={itemIndex}>
                  <span className="shrink-0 font-bold opacity-70">{itemIndex + 1}.</span>
                  <span>{renderInline(item, `${blockIndex}-${itemIndex}`, linkClass)}</span>
                </li>
              ))}
            </ol>
          );
        }
        return (
          <p key={blockIndex}>{renderInline(block.lines.join(" "), `p${blockIndex}`, linkClass)}</p>
        );
      })}
    </div>
  );
}
