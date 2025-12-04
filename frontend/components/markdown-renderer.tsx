import React from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeRaw from "rehype-raw"
import rehypeHighlight from "rehype-highlight"

export default function MarkdownRenderer({ children }: { children: string }) {
  return (
    <div className="prose prose-invert prose-cyan max-w-none text-white/80">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw, rehypeHighlight]}
        components={{
          code({node, inline, className, children, ...props}) {
            return !inline ? (
              <pre className={"bg-black/80 rounded-lg p-4 overflow-x-auto" + (className ? ` ${className}` : "")} {...props}><code>{children}</code></pre>
            ) : (
              <code className={"bg-black/40 rounded px-1 py-0.5" + (className ? ` ${className}` : "")} {...props}>{children}</code>
            )
          }
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  )
}
