import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-4 text-center">
          <div className="text-4xl">⚠️</div>
          <h2 className="text-xl font-bold text-text-primary">Something went wrong</h2>
          <p className="text-text-muted text-sm max-w-md">{this.state.error?.message}</p>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="px-4 py-2 bg-accent-cyan text-white rounded-lg text-sm hover:bg-accent-cyan/80"
          >
            Try Again
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
