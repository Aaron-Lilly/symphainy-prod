# Chatbot State Management - Simplified Usage

## 🎯 Single Source of Truth

You only need to use **one atom**: `mainChatbotOpenAtom`

All other states (transforms, positions, heights) derive automatically!

## 📝 Basic Usage

```typescript
import { useAtom } from 'jotai';
import { mainChatbotOpenAtom } from '@/shared/atoms';

function MyComponent() {
  const [mainChatbotOpen, setMainChatbotOpen] = useAtom(mainChatbotOpenAtom);
  
  return (
    <div>
      <button onClick={() => setMainChatbotOpen(true)}>
        Show Main Only
      </button>
      
      <button onClick={() => setMainChatbotOpen(false)}>
        Show Both Chatbots
      </button>
      
      <button onClick={() => setMainChatbotOpen(!mainChatbotOpen)}>
        Toggle
      </button>
    </div>
  );
}
```

## 🎭 Animation States

| `mainChatbotOpen` | Primary Chatbot | Secondary Chatbot |
|-------------------|-----------------|-------------------|
| `true` | Full height (87vh), normal position | Hidden (slides off-screen) |
| `false` | Partial height (70vh), slides down 20vh | Visible (slides in from right) |

## 🔧 Auto-Derived Atoms

These update automatically when `mainChatbotOpenAtom` changes:

```typescript
// You can read these, but never need to set them
const shouldShowSecondary = useAtomValue(shouldShowSecondaryChatbotAtom);
const primaryHeight = useAtomValue(primaryChatbotHeightAtom);
const primaryTransform = useAtomValue(primaryChatbotTransformAtom);
const secondaryPosition = useAtomValue(secondaryChatbotPositionAtom);
```

## ✅ That's It!

No complex action atoms, no multiple state updates needed.

Just set `mainChatbotOpenAtom` and everything else happens automatically! 🎉 