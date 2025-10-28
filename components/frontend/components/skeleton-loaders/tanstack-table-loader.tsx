import React from 'react';

const TableSkeleton = () => {
  return (
    <table className="min-w-full border-collapse">
      <thead>
        <tr>
          {[...Array(3)].map((_, index) => (
            <th key={index} className="border border-gray-400">
              <div
                className="h-4 bg-gray-300 animate-pulse"
                style={{ animationDelay: `${index * 0.1}s` }}
              />
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {[...Array(3)].map((_, rowIndex) => (
          <tr key={rowIndex}>
            {[...Array(3)].map((_, colIndex) => {
              const delay = rowIndex * 0.1 + colIndex * 0.1;
              return (
                <td key={colIndex} className="border border-gray-400">
                  <div
                    className="h-4 bg-gray-300 animate-pulse"
                    style={{ animationDelay: `${delay}s` }}
                  />
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default TableSkeleton;
