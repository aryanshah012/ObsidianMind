import React, { useState } from 'react';
import {
  X,
  Folder,
  GraduationCap,
  Cpu,
  BookOpen,
  Briefcase,
  Code,
  Sparkles,
  Plus,
  Loader2,
} from 'lucide-react';

const ICON_OPTIONS = [
  { id: 'Folder', label: 'General', icon: Folder },
  { id: 'GraduationCap', label: 'Academics', icon: GraduationCap },
  { id: 'Cpu', label: 'AI & Research', icon: Cpu },
  { id: 'BookOpen', label: 'Study & Reading', icon: BookOpen },
  { id: 'Briefcase', label: 'Work', icon: Briefcase },
  { id: 'Code', label: 'Engineering', icon: Code },
  { id: 'Sparkles', label: 'Creative', icon: Sparkles },
];

const COLOR_OPTIONS = [
  '#2E7D6A', // Emerald
  '#3B82F6', // Blue
  '#8B5CF6', // Purple
  '#EC4899', // Pink
  '#F59E0B', // Amber
  '#10B981', // Mint
  '#6366F1', // Indigo
];

export default function CreateVaultModal({ isOpen, onClose, onCreateVault }) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [icon, setIcon] = useState('Folder');
  const [color, setColor] = useState('#2E7D6A');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Workspace name is required.');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      await onCreateVault({
        name: name.trim(),
        description: description.trim(),
        icon,
        color,
      });
      setName('');
      setDescription('');
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to create workspace.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-fade-in font-sans">
      <div className="w-full max-w-md rounded-2xl bg-surface border border-border shadow-elevated p-6 space-y-5 animate-scale-up text-charcoal">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border/70 pb-3.5">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-sage-light text-sage flex items-center justify-center font-bold">
              <Plus className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold tracking-tight text-charcoal">
                Create New Workspace Vault
              </h2>
              <p className="text-xs text-charcoal-muted font-normal">
                Isolated notes, documents & vector index
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded-md text-charcoal-muted hover:text-charcoal hover:bg-canvas-subtle transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs font-mono">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Workspace Name */}
          <div className="space-y-1.5">
            <label className="block text-xs font-bold text-charcoal tracking-wide uppercase font-mono">
              Workspace Name <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              required
              placeholder="e.g., Biology 101, Quantum Computing, Work Specs"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-canvas-warm border border-border rounded-lg px-3.5 py-2 text-sm text-charcoal placeholder-charcoal-subtle focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage/40 transition-all font-sans"
            />
          </div>

          {/* Workspace Description */}
          <div className="space-y-1.5">
            <label className="block text-xs font-bold text-charcoal tracking-wide uppercase font-mono">
              Description (Optional)
            </label>
            <input
              type="text"
              placeholder="e.g., Lecture slides, research papers and problem sets"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-canvas-warm border border-border rounded-lg px-3.5 py-2 text-sm text-charcoal placeholder-charcoal-subtle focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage/40 transition-all font-sans"
            />
          </div>

          {/* Icon Picker */}
          <div className="space-y-1.5">
            <label className="block text-xs font-bold text-charcoal tracking-wide uppercase font-mono">
              Icon
            </label>
            <div className="grid grid-cols-7 gap-1.5">
              {ICON_OPTIONS.map((opt) => {
                const IconComp = opt.icon;
                const isSelected = icon === opt.id;
                return (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setIcon(opt.id)}
                    title={opt.label}
                    className={`h-9 rounded-lg flex items-center justify-center border transition-all ${
                      isSelected
                        ? 'bg-sage text-white border-sage shadow-xs scale-105'
                        : 'bg-canvas-warm text-charcoal-muted border-border hover:bg-surface-hover hover:text-charcoal'
                    }`}
                  >
                    <IconComp className="w-4 h-4" />
                  </button>
                );
              })}
            </div>
          </div>

          {/* Accent Color Picker */}
          <div className="space-y-1.5">
            <label className="block text-xs font-bold text-charcoal tracking-wide uppercase font-mono">
              Color Accent
            </label>
            <div className="flex items-center gap-2.5">
              {COLOR_OPTIONS.map((c) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => setColor(c)}
                  className={`w-6 h-6 rounded-full border transition-all ${
                    color === c
                      ? 'ring-2 ring-offset-2 ring-charcoal scale-110'
                      : 'hover:scale-105 border-black/10'
                  }`}
                  style={{ backgroundColor: c }}
                />
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="pt-2 flex items-center justify-end gap-2.5 border-t border-border/70">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-2 rounded-lg border border-border text-xs font-semibold text-charcoal hover:bg-surface-hover transition-colors"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={isSubmitting || !name.trim()}
              className="px-4 py-2 rounded-lg bg-sage hover:bg-sage-hover text-white text-xs font-semibold shadow-sm transition-all disabled:opacity-40 flex items-center gap-1.5"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Creating...</span>
                </>
              ) : (
                <span>Create Workspace</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
