export function TableSkeleton({ rows = 5, columns = 6 }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Header skeleton */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-700 dark:to-blue-800 p-4">
        <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
          {Array.from({ length: columns }).map((_, i) => (
            <div key={i} className="h-4 bg-blue-500 dark:bg-blue-600 rounded animate-pulse" />
          ))}
        </div>
      </div>

      {/* Rows skeleton */}
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={rowIndex} className="p-4">
            <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
              {Array.from({ length: columns }).map((_, colIndex) => (
                <div
                  key={colIndex}
                  className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"
                  style={{ animationDelay: `${(rowIndex * columns + colIndex) * 0.05}s` }}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function CardSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1 space-y-3">
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/3 animate-pulse" />
          <div className="h-8 bg-gray-300 dark:bg-gray-600 rounded w-1/2 animate-pulse" />
          <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded w-2/3 animate-pulse" />
        </div>
        <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse" />
      </div>
    </div>
  )
}

export function ChartSkeleton({ height = 300 }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-6 animate-pulse" />
      <div className="space-y-3" style={{ height }}>
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="flex items-end gap-2"
            style={{ height: `${100 / 5}%` }}
          >
            {Array.from({ length: 12 }).map((_, j) => (
              <div
                key={j}
                className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-t animate-pulse"
                style={{
                  height: `${Math.random() * 100}%`,
                  animationDelay: `${j * 0.1}s`
                }}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

export function HistogramSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4 animate-pulse" />
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4">
            <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse" />
            <div className="flex-1">
              <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse" style={{ animationDelay: `${i * 0.1}s` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function GaugeSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4 animate-pulse" />
      <div className="flex justify-center">
        <div className="w-64 h-32 bg-gray-200 dark:bg-gray-700 rounded-t-full animate-pulse" />
      </div>
      <div className="flex justify-center gap-4 mt-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16 animate-pulse" style={{ animationDelay: `${i * 0.1}s` }} />
        ))}
      </div>
    </div>
  )
}
