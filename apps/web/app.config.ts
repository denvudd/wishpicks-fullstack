export default defineAppConfig({
  ui: {
    colors: {
      primary: 'neutral',
    },

    button: {
      slots: {
        base: [
          'rounded-full',
          'font-medium',
          'cursor-pointer',
          'inline-flex items-center justify-center',
          'transition-all',
          'active:scale-[0.96]',
          'focus-visible:outline-none',
        ],
      },
      defaultVariants: {
        color: 'neutral',
        variant: 'solid',
        size: 'md',
      },
    },

    card: {
      slots: {
        root: [
          'bg-white dark:bg-black',
          'rounded-xl',
          'shadow-card',
          'ring-0 border-0',
          'overflow-hidden',
        ],
        body: 'p-6',
        header: 'px-6 pt-6',
        footer: 'px-6 pb-6',
      },
    },

    input: {
      slots: {
        base: [
          'rounded-lg',
          'bg-white dark:bg-black',
          'text-black dark:text-white',
          'placeholder:text-muted-gray',
          'focus:outline-none focus:ring-0',
          'w-full',
        ],
        root: ['w-full'],
      },
    },

    textarea: {
      slots: {
        base: [
          'rounded-lg',
          'bg-white dark:bg-black',
          'text-black dark:text-white',
        ],
        root: ['w-full'],
      },
    },

    radioGroup: {
      slots: {
        base: [
          'rounded-lg',
          'bg-white dark:bg-black',
          'text-black dark:text-white',
          'placeholder:text-muted-gray',
          'focus:outline-none focus:ring-0',
        ],
        indicator: 'animate-in fade-in transition-all duration-200 ease-out',
      },
    },

    select: {
      slots: {
        base: [
          'rounded-lg',
          'bg-white dark:bg-black',
          'text-black dark:text-white',
          'placeholder:text-muted-gray',
          'focus:outline-none focus:ring-0',
          'w-full',
        ],
      },
    },

    formField: {
      slots: {
        label: 'text-sm font-medium text-black dark:text-white mb-1',
      },
    },

    alert: {
      slots: {
        root: ['rounded-lg'],
      },
    },

    modal: {
      slots: {
        content:
          'rounded-xl! transition-[height,transform] duration-200 ease-out',
      },
    },
  },
})
