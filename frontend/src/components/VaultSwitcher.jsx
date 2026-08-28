import React, { useState, useRef, useEffect } from 'react';
import {
  ChevronDown,
  Folder,
  GraduationCap,
  Cpu,
  BookOpen,
  Briefcase,
  Code,
  Sparkles,
  Plus,
  Check,
  Trash2,
  Layers,
} from 'lucide-react';
import CreateVaultModal from './CreateVaultModal';

const ICON_MAP = {
  Folder: Folder,
  GraduationCap: GraduationCap,
  Cpu: Cpu,
  BookOpen: BookOpen,
  Briefcase: Briefcase,
  Code: Code,
  Sparkles: Sparkles,
};

export default function VaultSwitcher({
  vaults = [],
  activeVaultId,
  onSelectVault,
  onCreateVault,
  onDeleteVault,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const activeVault =
    vaults.find((v) => v.id === activeVaultId) ||
    vaults[0] || {
      id: 'default',
      name: 'Primary Vault',
      icon: 'Folder',
      color: '#2E7D6A',
      chunk_count: 0,
    };

  const ActiveIcon = ICON_MAP[activeVault.icon] || Folder;

  return (
    <div className="relative w-full" ref={dropdownRef}>
      {/* Active Vault Selector Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-2.5 rounded-xl bg-surface border border-border/90 hover:border-zinc-400 hover:shadow-card transition-all group select-none text-left"
      >
        <div className="flex items-center gap-2.5 min-w-0">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center text-white shrink-0 shadow-xs"
            style={{ backgroundColor: activeVault.color || '#2E7D6A' }}
          >
            <ActiveIcon className="w-4 h-4" />
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-bold text-charcoal truncate font-sans tracking-tight">
                {activeVault.name}
              </span>
            </div>
            <div className="flex items-center gap-1.5 font-mono text-[10.5px] text-charcoal-muted">
              <span>{activeVault.chunk_count || 0} vectors</span>
              <span>•</span>
              <span className="uppercase text-[9.5px] tracking-wider text-sage font-semibold">
                ACTIVE
              </span>
            </div>
          </div>
        </div>

        <ChevronDown
          className={`w-4 h-4 text-charcoal-muted transition-transform duration-200 shrink-0 ${
            isOpen ? 'rotate-180 text-charcoal' : ''
          }`}
        />
      </button>

      {/* Vault List Dropdown Menu */}
      {isOpen && (
        <div className="absolute left-0 top-full mt-2 w-full min-w-[280px] rounded-xl bg-surface border border-border shadow-elevated p-2 space-y-1.5 z-50 animate-fade-in font-sans">
          <div className="px-2.5 py-1.5 border-b border-border/70 flex items-center justify-between">
            <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-charcoal-muted flex items-center gap-1.5">
              <Layers className="w-3 h-3" />
              Workspaces ({vaults.length})
            </span>

            <button
              type="button"
              onClick={() => {
                setIsOpen(false);
                setIsModalOpen(true);
              }}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold text-sage hover:bg-sage-light transition-colors"
            >
              <Plus className="w-3 h-3" />
              <span>New</span>
            </button>
          </div>

          {/* Vault List */}
          <div className="max-h-60 overflow-y-auto custom-scrollbar space-y-1 pr-0.5">
            {vaults.map((vault) => {
              const IconComp = ICON_MAP[vault.icon] || Folder;
              const isActive = vault.id === activeVaultId;

              return (
                <div
                  key={vault.id}
                  className={`group/item flex items-center justify-between p-2 rounded-lg transition-all border ${
                    isActive
                      ? 'bg-sage-light/60 border-sage/30 text-charcoal font-medium'
                      : 'bg-transparent border-transparent text-charcoal-muted hover:bg-canvas-warm hover:text-charcoal'
                  }`}
                >
                  <button
                    type="button"
                    onClick={() => {
                      onSelectVault(vault.id);
                      setIsOpen(false);
                    }}
                    className="flex items-center gap-2.5 min-w-0 flex-1 text-left"
                  >
                    <div
                      className="w-6 h-6 rounded-md flex items-center justify-center text-white shrink-0 text-xs shadow-2xs"
                      style={{ backgroundColor: vault.color || '#2E7D6A' }}
                    >
                      <IconComp className="w-3.5 h-3.5" />
                    </div>

                    <div className="min-w-0 flex-1">
                      <div className="text-xs font-semibold truncate text-charcoal">
                        {vault.name}
                      </div>
                      <div className="text-[10px] font-mono text-charcoal-muted truncate">
                        {vault.description || `${vault.chunk_count || 0} indexed vectors`}
                      </div>
                    </div>
                  </button>

                  <div className="flex items-center gap-1 shrink-0 ml-1.5">
                    {isActive ? (
                      <Check className="w-4 h-4 text-sage" />
                    ) : !vault.is_default && onDeleteVault ? (
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (
                            window.confirm(
                              `Delete workspace "${vault.name}" and all its vector index data?`
                            )
                          ) {
                            onDeleteVault(vault.id);
                          }
                        }}
                        className="p-1 rounded text-charcoal-subtle hover:text-rose-600 hover:bg-rose-50 opacity-0 group-hover/item:opacity-100 transition-opacity"
                        title="Delete workspace"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    ) : null}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Bottom Action */}
          <div className="pt-1.5 border-t border-border/70">
            <button
              type="button"
              onClick={() => {
                setIsOpen(false);
                setIsModalOpen(true);
              }}
              className="w-full py-2 px-2.5 rounded-lg border border-dashed border-border hover:border-sage text-xs font-semibold text-charcoal flex items-center justify-center gap-1.5 hover:bg-sage-light/30 transition-colors"
            >
              <Plus className="w-3.5 h-3.5 text-sage" />
              <span>Create New Workspace</span>
            </button>
          </div>
        </div>
      )}

      {/* Modal */}
      <CreateVaultModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onCreateVault={onCreateVault}
      />
    </div>
  );
}
