   import React from "react";

   class ErrorBoundary extends React.Component {
       constructor(props) {
           super(props);
           this.state = { hasError: false };
       }

       static getDerivedStateFromError(error) {
           // Update state to trigger fallback UI
           return { hasError: true };
       }

       componentDidCatch(error, errorInfo) {
           // You can log the error to an error reporting service
           console.error("Error occurred in a component:", error, errorInfo);
       }

       render() {
           if (this.state.hasError) {
               // Fallback UI when an error occurs
               return <h2>Something went wrong. Please refresh the page.</h2>;
           }

           return this.props.children;
       }
   }

   export default ErrorBoundary;