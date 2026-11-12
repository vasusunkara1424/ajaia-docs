import type { Editor } from "@tiptap/react";
import type { ReactNode } from "react";

interface ToolProps {
  label: string;
  shortcut?: string;
  active?: boolean;
  onClick: () => void;
  children: ReactNode;
}

function Tool({ label, shortcut, active, onClick, children }: ToolProps) {
  return (
    <button
      type="button"
      className={`tool${active ? " tool--active" : ""}`}
      onMouseDown={(e) => e.preventDefault()} // keep editor selection
      onClick={onClick}
      aria-label={label}
      aria-pressed={active}
      title={shortcut ? `${label} (${shortcut})` : label}
    >
      {children}
    </button>
  );
}

const Divider = () => <span className="toolbar__divider" aria-hidden />;

type Block = "paragraph" | "h1" | "h2" | "h3";

export function Toolbar({ editor }: { editor: Editor }) {
  const chain = () => editor.chain().focus();

  const currentBlock: Block = editor.isActive("heading", { level: 1 })
    ? "h1"
    : editor.isActive("heading", { level: 2 })
      ? "h2"
      : editor.isActive("heading", { level: 3 })
        ? "h3"
        : "paragraph";

  const setBlock = (block: Block) => {
    if (block === "paragraph") chain().setParagraph().run();
    else chain().setHeading({ level: Number(block[1]) as 1 | 2 | 3 }).run();
  };

  return (
    <div className="toolbar" role="toolbar" aria-label="Formatting">
      <Tool label="Undo" shortcut="Ctrl+Z" onClick={() => chain().undo().run()}>↶</Tool>
      <Tool label="Redo" shortcut="Ctrl+Shift+Z" onClick={() => chain().redo().run()}>↷</Tool>
      <Divider />
      <select
        className="toolbar__select"
        value={currentBlock}
        onChange={(e) => setBlock(e.target.value as Block)}
        aria-label="Text style"
      >
        <option value="paragraph">Normal text</option>
        <option value="h1">Heading 1</option>
        <option value="h2">Heading 2</option>
        <option value="h3">Heading 3</option>
      </select>
      <Divider />
      <Tool label="Bold" shortcut="Ctrl+B" active={editor.isActive("bold")} onClick={() => chain().toggleBold().run()}>
        <b>B</b>
      </Tool>
      <Tool label="Italic" shortcut="Ctrl+I" active={editor.isActive("italic")} onClick={() => chain().toggleItalic().run()}>
        <i>I</i>
      </Tool>
      <Tool
        label="Underline"
        shortcut="Ctrl+U"
        active={editor.isActive("underline")}
        onClick={() => chain().toggleUnderline().run()}
      >
        <u>U</u>
      </Tool>
      <Tool label="Strikethrough" active={editor.isActive("strike")} onClick={() => chain().toggleStrike().run()}>
        <s>S</s>
      </Tool>
      <Divider />
      <Tool label="Bulleted list" active={editor.isActive("bulletList")} onClick={() => chain().toggleBulletList().run()}>
        • ≡
      </Tool>
      <Tool label="Numbered list" active={editor.isActive("orderedList")} onClick={() => chain().toggleOrderedList().run()}>
        1. ≡
      </Tool>
      <Tool label="Quote" active={editor.isActive("blockquote")} onClick={() => chain().toggleBlockquote().run()}>
        ❝
      </Tool>
      <Divider />
      <Tool label="Clear formatting" onClick={() => chain().unsetAllMarks().clearNodes().run()}>
        T̸
      </Tool>
    </div>
  );
}
